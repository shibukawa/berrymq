module BerryMQ
  #
  #Library user includes this module to enable method callback.
  #After including, you can use decorator methods. see FollowerAPI module.
  #
  module Follower
    def self.included(base)
      base.extend(FollowerAPI)
    end
    def initialize
      BerryMQ::DecoratorManager.decorate_object(self)
    end
  end

  module FollowerAPI
    def following(identifier, &guard_condition)
      id_obj = BerryMQ::Identifier.new(identifier, guard_condition)
      BerryMQ::DecoratorManager::new_decorator(self, :following, id_obj, [])
    end

    def auto_twitter(identifier)
      id_obj = BerryMQ::Identifier.new(identifier)
      if id_obj.action != nil
        args = [id_obj.action.include?("entry"), id_obj.action.include?("exit")]
      else
        args = [true, true]
      end
      BerryMQ::DecoratorManager::new_decorator(self,:auto_twitter,id_obj,args)
    end

    def method_added(method)
      BerryMQ::DecoratorManager::method_added(self, method)
    end
  end

  class Cond
  end

  def self.twitter(id, *args)
    id_obj = BerryMQ::Identifier.new(id)
    if args.last.kind_of?(Hash)
      kwargs = args.pop
    else
      kwargs = {}
    end
    BerryMQ::RootTransporter::twitter(id_obj, args, kwargs)
  end

  def self.show_followers
    BerryMQ::RootTransporter::show_followers
  end
end
