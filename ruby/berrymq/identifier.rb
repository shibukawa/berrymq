require 'set'

module BerryMQ
  #
  #= Message address identifier
  #
  #This class analyzes and checks matching address.
  #The address is used for filtering received message.
  #
  #== Address Sample
  #
  #* Basic Format
  #  "name:action"
  #* Name Only
  #  "name"
  #* Local Message(not forword to other processes/machines)
  #  "_name", "_name:action"
  #* Namespace
  #  "name@namespace:action"
  #* Wildcard
  #  "*:action", "name:*", "*:*", "*@namespace:action"
  class Identifier
    attr_reader :name, :action, :namespace
    def initialize(key_or_identifier, action=nil)
      @functions = [nil, nil]
      if action != nil
        @name = key_or_identifier.name
        @namespace = key_or_identifier.namespace
        @action = Set.new [action]
        @functions[0] = method :_match_all
        return
      end
      name, @namespace, action = _split_key(key_or_identifier)
      if name == "*" && action == "*"
        @name = @action = nil
        @functions[0] = method :_match_always
      elsif name == "*" && action != "*"
        @name = nil
        @action = Set.new [action]
        @functions[0] = method :_match_action_only
      elsif name != "*" && action == "*"
        @name = name
        @action = nil
        @functions[0] = method :_match_name_only
      elsif name != "*" && action != "*"
        @name = name
        @action = Set.new [action]
        @functions[0] = method :_match_all
      end
      @functions[1] = method :_match_always
    end

    def _split_key(key)
      if /(.*):(.*)/ =~ key
        name = $1
        action = $2
      else
        name = key
        action = "*"
      end
      if /(.*)@(.*)/ =~ name
        name = $1
        namespace = $2
      else
        namespace = nil
      end
      return [name, namespace, action]
    end

    def guard(&condition)
      @functions[1] = condition
    end

    def to_s
      "<BerryMQ::Identifier object at %d: id=%s>" % [self.object_id, id_str()]
    end

    def id_str
      name = @name || "*"
      action = @action != nil ? @action.to_a.sort.join(",") : "*"
      "%s:%s" % [name, action]
    end

    def _match_all(rhs)
      _match_name_only(rhs) && _match_action_only(rhs)
    end

    def _match_name_only(rhs)
      return true if self.name == nil or rhs.name == nil
      self.name == rhs.name
    end

    def _match_always(p)
      true
    end

    def _match_action_only(rhs)
      return true if rhs.action == nil
      !(self.action & rhs.action).empty?
    end

    def is_match(expose_identifier, message=nil)
      if @functions[0].call(expose_identifier)      
        @functions[1].call(message) 
      else
        false
      end
    end

    def is_local
      @name.slice(0,1) == "_"
    end
  end
end
